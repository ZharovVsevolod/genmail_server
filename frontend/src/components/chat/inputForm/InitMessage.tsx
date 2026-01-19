import React from "react";

interface InitMessageProps {
    userName: string | null;
}

const InitMessage: React.FC<InitMessageProps>= ({userName}) => {
    return (
        <>
            <div className="greeting-text">
                <div className="greeting-line1">Привет{userName? ` ${userName}` : ""}, я Элис!</div>
                <div className="greeting-line2">Чем я могу помочь?</div>
            </div>
            <div className="onboarding-cards">
                <div className="onboarding-card">
                    <div className="onboarding-card-content">
                        <div className="onboarding-card-text">
                            <div className="onboarding-card-title">Проанализировать документ</div>
                            <div className="onboarding-card-body">и дать его основную суть в кратком резюме</div>
                        </div>
                        <div className="onboarding-card-image">
                            <img src="/onboarding1.png" alt="Onboarding" />
                        </div>
                    </div>
                </div>
                <div className="onboarding-card">
                    <div className="onboarding-card-content">
                        <div className="onboarding-card-text">
                            <div className="onboarding-card-title">Подготовить ответ для клиента</div>
                            <div className="onboarding-card-body">на основе внутренней базы знаний</div>
                        </div>
                        <div className="onboarding-card-image">
                            <img src="/onboarding2.png" alt="Onboarding" />
                        </div>
                    </div>
                </div>
                <div className="onboarding-card">
                    <div className="onboarding-card-content">
                        <div className="onboarding-card-text">
                            <div className="onboarding-card-title">Помочь с технической документацией</div>
                            <div className="onboarding-card-body"></div>
                        </div>
                        <div className="onboarding-card-image">
                            <img src="/onboarding3.png" alt="Onboarding" />
                        </div>
                    </div>
                </div>
            </div>
        </>
    )
};

export default InitMessage;